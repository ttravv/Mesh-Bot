class HomeworksWrap:
    @staticmethod
    def build(homeworks):
        res_dict = {}
        for homework in homeworks:
            if homework.subject_name in res_dict.keys():
                res_dict[homework.subject_name].append(homework)
            else:
                res_dict[homework.subject_name] = [homework]
        res_str = "🎓 **Домашние задания:**\n"  
        for key, value in res_dict.items():
            res_str += f"\n🌟 **{key}:**\n"  
            for hw in value:
                status = "✔️" if hw.is_done else "❌"
                res_str += f"   - {hw.description} ({status})\n" 

        res_str += "\n✨ Успехов в учебе!"  
        return res_str.strip() 
    


